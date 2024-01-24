package extractmethodrunner;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.function.Consumer;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspace;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.ICoreRunnable;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.compiler.IProblem;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTRequestor;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.refactoring.CompilationUnitChange;
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.text.edits.DeleteEdit;
import org.eclipse.text.edits.TextEdit;

/**
 * This class controls all aspects of the application's execution
 */
@SuppressWarnings("restriction")
public class DeleteAnnotationsApplication implements IApplication {

	void files(IResource[] dirs, Consumer<IFile> f) throws CoreException {
		for (IResource r : dirs) {
			if (r.getType() == IResource.FILE) {
				f.accept((IFile) r);
			} else if (r.getType() == IResource.FOLDER) {
				files(((IFolder) r).members(), f);
			}
		}
	}

	@Override
	public Object start(IApplicationContext context) throws Exception {
		IProgressMonitor pm = new NullProgressMonitor();
		IWorkspace ws = ResourcesPlugin.getWorkspace();

		Map<?, ?> args = context.getArguments();
		String[] argArray = (String[]) args.get("application.args");
		int idx = 0;
		while (!"-projects".equals(argArray[idx++]))
			;
		String[] projects = argArray[idx].split(",");

		ws.run(new ICoreRunnable() {

			@Override
			public void run(IProgressMonitor monitor) throws CoreException {
				class ChangeWithPos {
					Change change;
					int startOffset;
					
					public ChangeWithPos(Change change, int startOffset) {
						super();
						this.change = change;
						this.startOffset = startOffset;
					}
					
					private int isAfter(ChangeWithPos o) {
						return o.startOffset - startOffset;
					}
				}
				
				for (String project : projects) {
					IProject code = ws.getRoot().getProject(project);
					System.err.println("project at " + code.getRawLocation());
					code.open(pm);
					IJavaProject javaProject = JavaCore.create(code);
					files(code.members(), f -> {
						if (f.getName().endsWith(".java")) {
							SortedSet<ChangeWithPos> deletes = new TreeSet<ChangeWithPos>(new Comparator<ChangeWithPos>() {
								@Override
								public int compare(ChangeWithPos o1, ChangeWithPos o2) {
									return o1.isAfter(o2);
								}
							});

							@SuppressWarnings("deprecation")
							final ASTParser parser = ASTParser.newParser(AST.JLS8);
							parser.setResolveBindings(true);
							parser.setProject(javaProject);
							System.err.println(f);
							ICompilationUnit icu = JavaCore.createCompilationUnitFrom(f);
							parser.createASTs(new ICompilationUnit[] { icu }, new String[0], new ASTRequestor() {
								@Override
								public void acceptAST(ICompilationUnit source, CompilationUnit ast) {
									for (IProblem p : ast.getProblems()) {
										if (p.isError()) {
											return;
										}
									}

									ast.accept(new ASTVisitor() {
										@SuppressWarnings("unchecked")
										public boolean visit(MethodDeclaration node) {
											for(Object x : node.modifiers()) {
												if (x instanceof Annotation) {
													Annotation togo = (Annotation)x;
													TextEdit edit = new DeleteEdit(togo.getStartPosition(), togo.getLength());
													CompilationUnitChange c = new CompilationUnitChange("add change comment", icu);
													c.setEdit(edit);
													deletes.add(new ChangeWithPos(c, togo.getStartPosition()));
												}
											}
											return super.visit(node);
										}

									});
								}
							}, pm);

							try {
								f.refreshLocal(1, monitor);
							} catch (CoreException e1) {
								System.err.println(e1);
								e1.printStackTrace(System.err);
								assert false : e1;		
							}
							
							deletes.forEach(c -> { 
								try {
									c.change.perform(monitor);
									System.err.println("deleted " + Arrays.toString(c.change.getAffectedObjects()));
								} catch (CoreException e) {
									System.err.println(e);
									e.printStackTrace(System.err);
									assert false : e;		
								}
							});
						}
					});
				}
			}
		}, pm);

		ws.save(true, pm);

		return IApplication.EXIT_OK;
	}

	@Override
	public void stop() {
		// nothing to do
	}
}
