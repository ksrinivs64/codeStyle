/*
 * Copyright (c) 2002 - 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package extractmethodrunner;

import java.io.IOException;
import java.util.List;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.regex.Pattern;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Block;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.internal.corext.refactoring.code.ExtractMethodRefactoring;
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.ltk.core.refactoring.RefactoringStatus;

@SuppressWarnings("restriction")
public class ExtractMethods extends ASTHelper {
	private static final Pattern extractedName = Pattern.compile("extracted_[0-9]+");

	private static int maxIndex;

	public static SortedSet<Extraction> extractMethods(CompilationUnit ast, IProgressMonitor pm) throws IOException {
		SortedSet<Extraction> found = new TreeSet<>();
		
		maxIndex = -1;
		
		ast.accept(new ASTVisitor() {
			
			@Override
			public boolean visit(MethodDeclaration node) {
				SimpleName nm = node.getName();
				String str = nm.getIdentifier();
				if (extractedName.matcher(str).matches()) {
					int idx = Integer.parseInt(str.substring("extracted_".length()));
					if (idx > maxIndex) {
						maxIndex = idx;
					}
				}
				
				return super.visit(node);
			}
		});
		
		ast.accept(new ASTVisitor() {
			
			@Override
			public boolean visit(Block node) {
				@SuppressWarnings("rawtypes")
				List stmts = node.statements();
				if (stmts.size() > 3) {
					
					for(int firstIdx = 0; firstIdx < stmts.size() - 1 && found.isEmpty(); firstIdx++) 	{			
						Statement first = (Statement) stmts.get(firstIdx);
						int start = first.getStartPosition();
						for(int i = stmts.size()-1; i > firstIdx; i--) {
							Statement last = (Statement) stmts.get(i);
							int length = last.getStartPosition() + last.getLength() - start;
							Extraction e;
							if ((e = extractableMethod(pm, ast, start, length)) != null) {
								found.add(e);
							}
						}
					}
					
					return found.isEmpty();
				} else {
					return true;
				}
			}
		});
		
		return found;
	}
	
	public static Extraction extractableMethod(IProgressMonitor pm, CompilationUnit icu, int selectionStart, int selectionLength) {
		ExtractMethodRefactoring x = new ExtractMethodRefactoring(icu, selectionStart, selectionLength);
		x.setReplaceDuplicates(true);
		try {
			RefactoringStatus s = x.checkAllConditions(pm);
			if (s.isOK() && x.getNumberOfDuplicates() > 0) {
				System.out.println(s + " with " + x.getNumberOfDuplicates() + " duplicates");
				x.setMethodName("extracted_" + ++maxIndex);
				Change c = x.createChange(pm);
				Extraction e =  new Extraction() {

					@Override
					public int start() {
						return selectionStart;
					}

					@Override
					public int end() {
						return start() + selectionLength;
					}

					@Override
					public Change change() {
						return c;
					}	
				};		
		        
			return e;
			} 

		} catch (Exception e) {
			System.err.println(e);
		}

		return null;
	}
}
