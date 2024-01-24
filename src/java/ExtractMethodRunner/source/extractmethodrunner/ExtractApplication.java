package extractmethodrunner;

import java.io.IOException;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
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
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.refactoring.CompilationUnitChange;
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.text.edits.InsertEdit;
import org.eclipse.text.edits.TextEdit;

/**
 * This class controls all aspects of the application's execution
 */
public class ExtractApplication implements IApplication {

	void files(IResource[] dirs, Consumer<IFile> f) throws CoreException {
		for(IResource r : dirs) {
			if (r.getType() == IResource.FILE) {
				f.accept((IFile)r);
			} else if (r.getType() == IResource.FOLDER) {
				files(((IFolder)r).members(), f);
			}
		}		
	}

	@Override
	public Object start(IApplicationContext context) throws Exception {
		IProgressMonitor pm = new NullProgressMonitor();
		IWorkspace ws = ResourcesPlugin.getWorkspace();

		Map<?,?> args = context.getArguments();
		String[] argArray = (String[])args.get("application.args");
		int idx = 0;
		while (! "-projects".equals(argArray[idx++]));
		String[] projects = argArray[idx].split(",");

		ws.run(new ICoreRunnable() {

			@Override
			public void run(IProgressMonitor monitor) throws CoreException {
				for(String project : projects) {
					IProject code = ws.getRoot().getProject(project);
					code.open(pm);
					IJavaProject javaProject = JavaCore.create(code);
					Set<ICompilationUnit> changedFiles = new LinkedHashSet<>(); 

					files(code.members(), f -> { 
						if (f.getName().endsWith(".java")) {
							@SuppressWarnings("deprecation")
							final ASTParser parser = ASTParser.newParser(AST.JLS8);
							parser.setResolveBindings(true);
							parser.setProject(javaProject);
							System.err.println(f);
							ICompilationUnit icu = JavaCore.createCompilationUnitFrom(f);
							SortedSet<Extraction> found = new TreeSet<>();
							parser.createASTs(new ICompilationUnit[] { icu }, 
									new String[0], 
									new ASTRequestor() {
										@Override
										public void acceptAST(ICompilationUnit source, CompilationUnit ast) {
											try {
												for (IProblem p : ast.getProblems()) {
													if (p.isError()) {
														return;
													}
												}
												found.addAll(ExtractMethods.extractMethods(ast, monitor));
											} catch (IOException e) {
												assert false : e;
											}
										}
								},
								monitor);
							
							Extraction e = null;
							int length = 0;
							for(Extraction i : found) {
								if (i.end() - i.start() > length) {
									e = i;
									length = e.end() - e.start();
								}
							}
							
							if (e != null) {
								try {
									Change c = e.change();
									if (c instanceof CompilationUnitChange) {
										ICompilationUnit cu = ((CompilationUnitChange) c).getCompilationUnit();
										if (! changedFiles.contains(cu)) {
											changedFiles.add(cu);
										}
									}
									c.perform(pm);
									
									f.refreshLocal(1, monitor);
									TextEdit edit = new InsertEdit(0, "// file changed\n");
									CompilationUnitChange cc = new CompilationUnitChange("add change comment", icu);
									cc.setEdit(edit);
									cc.perform(pm);
									
								} catch (CoreException e1) {
									e1.printStackTrace(System.err);
								}
							}
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
